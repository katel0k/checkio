import React, {useEffect} from 'react';
import ReactDOM from 'react-dom';
const { io } = require("socket.io-client");
const socket = io();

// const url = new URL(`http://localhost:5000/room/${room_id}/`);
// const url = 
// console.log(url);
// console.log(new URL('game', url));

const waiting_state = 'waiting';
const accept_state = 'accept';
const playing_state = 'playing';

class App extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            state: waiting_state
        }
    }
    componentDidMount() {
        fetch(new URL('info', location.href)).then(response => response.json())
        .then(obj => {
            console.log(obj, this);
            this.setState({
                state: obj.state,
                room_id: obj.id
            });
            return obj;
            // this.setState({
            //     field: obj.field,
            //     order: obj.order,
            //     player1Info: obj.player1,
            //     player2Info: obj.player2,
            //     playerColor: obj.player_color
            // });
        }).then(obj => {
            console.log(obj);
            socket.emit('join', obj.id);
        });
        
        socket.on('ready_to_start', (...args) => {
            this.setState({
                state: playing_state
            });
        });
        // socket.on('')
        // socket.on('both_players_joined', (...args) => {
        //     this.setState({
        //         state: playing_state
        //     });
        // });

        // socket.on('player_left', (...args) => {

        // });
    }
    render () {
        switch (this.state.state) {
            case waiting_state:
                return (<WaitingState room_id={this.state.room_id}/>);
            // case 'accept':
            //     return (<AcceptanceWaitingState/>);
            case playing_state:
                return (<PlayingState room_id={this.state.room_id}/>);
        }
    }

}


function CheckerImg ({ghost, color, queen}) {
	return <img className={"checkers-img" + (ghost ? ' checkers-img-ghost' : '') }
		src={`/client/img/${color ? 'white' : 'black'}${queen ? '-queen' : ''}.png`}
		alt={color ? 'wh' : 'bl'}/>
}

function CheckersCell ({checker, bg, pos}) {
    return (
        <div className={`checkers-cell checkers-cell-${bg}`}
                pos={pos}>
            {checker.is_empty ? undefined : <CheckerImg 
                    color={checker.color}
                    queen={checker.queen}

                    />}
        </div>
    )
}

class CheckersField extends React.Component {
	render () {
        // console.log(this.props.field);
		return (
			<div className="checkers-field" onClick={this.props.onClick}>
				{this.props.field.reduce((arr, el, i) => 
					arr.concat(el.map((value, j) => 
						<CheckersCell
							key={i + '_' + j}
							pos={i + '_' + j}
							checker={value}
							bg={(i + j) % 2 == 0 ? 'white' : 'black'}
						/>
						)), [])}
			</div>
			)
	}
}

// HOC for checkers
function CheckersUI ({activePlayer, ...passThrough}) {
	const ABC = 'abcdefgh';
	let cl = activePlayer === 'black' ? ' reverse' : '';
	return (
		<div className="checkers-UI">
			<div className={"checkers-UI__top-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{a}</span>)}
			</div>
			<div className={"checkers-UI__left-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{i+1}</span>)}
			</div>
			<div className={"checkers" + cl}> <CheckersField {...passThrough}/> </div>
			<div className={"checkers-UI__right-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{i+1}</span>)}
			</div>
			<div className={"checkers-UI__bottom-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{a}</span>)}
			</div>
		</div>
		);
}

class CheckersGame extends React.Component {
    render () {
        return (
        <div className="game">
            <div className="game-stats-container">
                {/* <GameStats
                    order={this.state.game.order} /> */}
            </div>
            <div className="checkers-UI-container">
                <CheckersUI
                    activePlayer={'white'}
                    onClick={this.props.handleCheckersClick}
                    field={this.props.field} />
            </div>
        </div>
        );
    }
}

/// pasted from previous project, untested -----------------------------------------------------------------

// class WaitingState extends React.Component {
//     constructor(props) {
//         super(props);
        
//     }
//     render() {
//         return (<div>Waiting</div>);
//     }
// }

function PlayerInfo(props) {
    return (<div></div>);
}

class PlayingState extends React.Component {
    constructor (props) { 
        super(props);
        this.state = {
            player1: undefined,
            player2: undefined,
            field: [],
            fieldSelected: false,
            playerColor: true,
            room_id: props.room_id
        };
    }
    componentDidMount() {
        fetch(new URL('game', location.href)).then(response => response.json())
        .then(obj => {
            this.setState({
                field: obj.field,
                order: obj.order,
                whitePlayerInfo: obj.white_player,
                blackPlayerInfo: obj.black_player,
                playerColor: obj.player_color
            });
        });
        socket.on('made_move', (json) => {
            let {field, move, order, ...rest} = JSON.parse(json);
            console.log(field, move, this);
            if (!move.is_possible) {
                // display error message
                this.setState({
                    fieldSelected: false
                });
                return;
            }
            this.setState({
                field: field,
                order: order,
                fieldSelected: false
            });
        });
    }

    handleCheckersClick(e) {
        console.log(this.state);
        let [row, col] = [...e.target.closest('.checkers-cell')
						.getAttribute('pos').split('_').map(Number)];
        if (this.state.fieldSelected) {
            if (this.state.field[this.state.fieldSelected.y][this.state.fieldSelected.x].is_empty) {
                this.setState({
                    fieldSelected: false
                });
                return;
            }
            else if (col == this.state.fieldSelected.x && row == this.state.fieldSelected.y) {
                return;
            }
            let move = {
                x0: this.state.fieldSelected.x,
                y0: this.state.fieldSelected.y,
                x: col,
                y: row,
                player_color: this.state.playerColor
            };
            console.log(move);
            socket.emit('made_move', this.state.room_id, move);
        }
        else {
            if (!this.state.field[row][col].is_empty) {
                this.setState({
                    fieldSelected: {x: col, y: row}
                });
            }
        }
    }
    render () {
        return (
        <div className="app-container">
            <div className="app">
                <div className="player-container player1">
                    <PlayerInfo info={this.state.player1}/>
                </div>
                <div className="game-container">
                    <span>{this.state.order ? 'white' : 'black'}</span>
                    <CheckersGame field={this.state.field} 
                            handleCheckersClick={this.handleCheckersClick.bind(this)} />
                </div>
                <div className="player-container player2">
                    <PlayerInfo info={this.state.player2}/>
                </div>
            </div>
        </div>
        );
    }
}

class WaitingState extends React.Component {
    constructor (props) { super(props); }
    // componentDidMount() {
    //     socket.on('ready_to_start', (...args) => {
            
    //     });
    // }
    handleAccept (player) {
        // player == true - белый игрок, false - черный
        socket.emit('join_game', this.props.room_id);
    }
    render () {
        return (
            <div className="form-wrapper">
                <button onClick={this.handleAccept.bind(this)}>Зайти за черных</button>
                <button onClick={this.handleAccept.bind(this)}>Зайти за белых</button>
                {/* <form action="join"><input type="submit" value="Зайти за черных"/></form> */}
                {/* <form action="join"><input type="submit" value="Зайти за белых"/></form> */}
            </div>
        )
    }
}

ReactDOM.render(<App/>, document.querySelector('.__react-root'));