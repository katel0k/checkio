import React from 'react';

function CheckerImg ({is_ghost, is_white, is_queen}) {
	return <img className={"checkers-img" + (is_ghost ? ' checkers-img-ghost' : '') }
		src={`/client/img/${is_white ? 'white' : 'black'}${is_queen ? '-queen' : ''}.png`}
		alt={is_white ? 'wh' : 'bl'}/>
}

function CheckersCell ({checker, bg, pos}) {
    return (
        
        <div className={`checkers-cell checkers-cell-${bg}`}
                pos={pos}>
            {checker.is_empty ? undefined : <CheckerImg 
                    is_white={checker.is_white}
                    is_queen={checker.is_queen}

                    />}
        </div>
    )
}

function CheckersField(props) {
    return (
        <div className="checkers-field" onClick={props.onClick}>
            {props.field.reduce((arr, el, i) => 
                arr.concat(el.map((value, j) => 
                    <CheckersCell
                        key={i + '_' + j}
                        pos={i + '_' + j}
                        checker={value}
                        bg={(i + j) % 2 == 0 ? 'white' : 'black'}
                    />
                    )), [])}
        </div>
        );
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

export default class CheckerGame extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            field: [],
            order: true,
            fieldSelected: undefined
        }
    }

    componentDidMount() {
        fetch(new URL('game', location.href))
            .then(response => response.json())
            .then(obj => {
                this.setState({
                    field: obj.field,
                    order: obj.order
                })
            });

        this.props.socket.on('made_move', (json) => {
            let {field, move, ...rest} = JSON.parse(json);
            // console.log(field, move, this);
            if (!move.is_possible) {
                // display error message
                this.setState({
                    fieldSelected: false
                });
                return;
            }
            console.log(field);
            this.setState({
                field: field,
                order: move.changes_order ^ move.is_white_player,
                fieldSelected: false
            });
        });
    }

    handleCheckersClick(e) {
        // console.log(this.state);
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
                player_color: this.props.playerColor == 'white'
            };
            // console.log(move);
            this.props.socket.emit('made_move', this.props.roomId, move);
        }
        else {
            if (!this.state.field[row][col].is_empty) {
                this.setState({
                    fieldSelected: {x: col, y: row}
                });
            }
        }
    }

    render() {
        return (
            <div className="game">
                <div className="game-stats-container">
                    <span>order: {this.state.order ? 'white' : 'black'}</span>
                    <span>color: {this.props.playerColor}</span>
                </div>
                <div className="checkers-UI-container">
                    <CheckersUI
                        onClick={this.handleCheckersClick.bind(this)}
                        field={this.state.field} />
                </div>
            </div>
        )
    }
}