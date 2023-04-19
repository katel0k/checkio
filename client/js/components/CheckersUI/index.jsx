

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

function CheckersField() {
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

export default function CheckersGame(props) {
    return (
    <div className="game">
        <div className="game-stats-container">
            {/* <GameStats
                order={this.state.game.order} /> */}
        </div>
        <div className="checkers-UI-container">
            <CheckersUI
                activePlayer={'white'}
                onClick={props.handleCheckersClick}
                field={props.field} />
        </div>
    </div>
    );
}