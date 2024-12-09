import React from 'react';

function CheckerImg ({is_ghost, is_white, is_queen}) {
	return <img className={"checkers-img" + (is_ghost ? ' checkers-img-ghost' : '') }
		src={`/client/img/${is_white ? 'white' : 'black'}${is_queen ? '-queen' : ''}.png`}
		alt={is_white ? 'wh' : 'bl'}/>
}

function CheckersCell ({checker, bg, pos, selected}) {
    return (
        <div className={`checkers-cell checkers-cell-${bg} ${selected ? 'checkers-cell-selected' : ''}`}
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
            {props.field.reduce((arr, el, y) => 
                arr.concat(el.map((value, x) => 
                    <CheckersCell
                        key={y + '_' + x}
                        pos={y + '_' + x}
                        checker={value}
                        bg={(y + x) % 2 == 0 ? 'white' : 'black'}
                        selected={props.fieldSelected ? props.fieldSelected.x == x && props.fieldSelected.y == y : false}
                    />
                    )), [])}
        </div>
        );
}

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
                    field: obj.game.field,
                    order: obj.game.is_white_move
                });
            });

        this.props.socket.on('made_move', (json) => {
            let {game, move} = JSON.parse(json);
            this.setState({
                field: game.field,
                order: game.is_white_move,
                fieldSelected: undefined
            });
        });
    }

    handleCheckersClick(e) {
        let [row, col] = [...e.target.closest('.checkers-cell')
						.getAttribute('pos').split('_').map(Number)];

        let is_white_player = this.props.playerColor == undefined ?
            undefined : this.props.playerColor == 'white';

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
                player_color: is_white_player
            };
            this.props.socket.emit('made_move', move);
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
                        field={this.state.field}
                        fieldSelected={this.state.fieldSelected} />
                </div>
            </div>
        )
    }
}
