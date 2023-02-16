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
    render () {
        return (this.state.state.render());
    }
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
                {/* <CheckersUI
                    activePlayer={'white'}
                    onClick={this.handleCheckersClick}
                    field={this.engine(this.state.tb)} /> */}
            </div>
        </div>
        );
    }
}

class State {
    constructor (props) {

    }
    render (props) {

    }
}

class WaitingState extends State {
    constructor (props) { super(props); }
    render () {
        
    }
}

class PlayingState extends State  {
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

class BrokenGameState extends State {
    constructor (props) { super(props); }
}

class EndGameState extends State  {
    constructor (props) { super(props); }
}

class AcceptanceWaitingState extends State {
    constructor (props) { super(props); }

}

ReactDOM.render(<App state={new PlayingState()}/>, document.querySelector('.__react-root'));