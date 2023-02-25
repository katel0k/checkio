import React from 'react';
import ReactDOM from 'react-dom';
const { io } = require("socket.io-client");
const socket = io();

class App extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            state: props.state
        }
    }
    componentDidMount() {
        socket.of('/room').emit('join');

        socket.of('/room').on('both_players_joined', (...args) => {
            this.setState({
                state: AcceptanceWaitingState()
            });
        });

        socket.of('/room').on('player_left', (...args) => {

        });
    }
    render () {
        return (this.state.state.render());
    }
}

/// pasted from previous project, untested -----------------------------------------------------------------

function CheckerImg ({ghost, color, queen}) {
	return <img className={"checkers-img" + (ghost ? ' checkers-img-ghost' : '') }
		src={color + (queen ? '-queen' : '') + '.png'}
		alt={color === 'white' ? 'wh' : 'bl'}/>
}

function CheckersCell ({checker, bg, pos, state}) {
	checker = (checker || state & 4) ? <CheckerImg 
		ghost={state & 4}
		color={checker.color}
		queen={checker.queen || state & 8} /> : undefined;
	return (
		<div className={'checkers-cell checkers-cell-' + bg + 
				(state & 1 ? ' checkers-cell-movable' : '') +
				(state & 2 ? ' checkers-cell-checked' : '')
				} 
			pos={pos}>
			{checker}
		</div>
		)
}

class CheckersField extends React.Component {
	render () {
		// let checked = (i, j) => this.props.checked && (i === this.props.checked.row) && (j === this.props.checked.col);
		return (
			<div className="checkers-field" onClick={this.props.onClick}>
				{this.props.field.reduce((arr, el, i) => 
					arr.concat(el.map(({value, state}, j) => 
						<CheckersCell
							key={i + '_' + j}
							pos={i + '_' + j}
							checker={value}
							state={state}
							bg={(i + j) % 2 === 0 ? 'white' : 'black'}
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
			<div className={"checkers" + cl}> <Checkers {...passThrough}/> </div>
			<div className={"checkers-UI__right-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{i+1}</span>)}
			</div>
			<div className={"checkers-UI__bottom-letters checkers-UI__letters" + cl}>
				{ABC.split('').map((a, i) => <span className="checkers-UI__letter" key={i}>{a}</span>)}
			</div>
		</div>
		)
}

class CheckersGame extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            field: []
        };
    }
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
                    onClick={this.handleCheckersClick}
                    field={this.engine(this.state.tb)} />
            </div>
        </div>
        );
    }
}

/// pasted from previous project, untested -----------------------------------------------------------------

class WaitingState extends React.Component {
    constructor(props) {
        super(props);
        
    }
    render() {

    }
}

class PlayingState extends React.Component {
    constructor (props) { super(props); }
    render () {
        return (
        <div className="app-container">
            <div className="app">
                <div className="player-container player1">
                    {/* <PlayerInfo
                        player={this.state.player2}
                        field={this.state.game.field}
                        history={this.state.game.history || []} /> */}
                </div>
                <div className="game-container">
                    <CheckersGame />
                </div>
                <div className="player-container player2">
                    {/* <PlayerInfo
                        player={this.state.player1}
                        field={this.state.game.field}
                        history={this.state.game.history || []} 
                        reverse={true} /> */}
                </div>
            </div>
        </div>
        );
    }
}

class BrokenGameState extends React.Component {
    constructor (props) { super(props); }
}

class EndGameState extends React.Component  {
    constructor (props) { super(props); }
}

class AcceptanceWaitingState extends React.Component {
    constructor (props) { super(props); }
    render () {
        return (
            <div className="form-wrapper">
                <form action="leave"><input type="submit" value="Выйти из игры"/></form>
                <form action="agree"><input type="submit" value="Принять игру"/></form>
            </div>
        )
    }

}

ReactDOM.render(<App state={new PlayingState()}/>, document.querySelector('.__react-root'));