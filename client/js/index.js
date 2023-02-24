import React from 'react';
import ReactDOM from 'react-dom';
// const { io } = require("socket.io-client");
// const socket = io();

class App extends React.Component {
    constructor (props) {
        super(props);
    }
    render () {
        return (<div className="main-page-wrapper">
            <div className="main-page">
                <div className="toolbar-wrapper">
                    <Toolbar />
                </div>
                <div className="rooms-wrapper">
                    <Rooms />
                </div>
            </div>
        </div>);
    }
}

class Rooms extends React.Component {
    render() {
        return (<div className="rooms">

                </div>);
    }
}

class Toolbar extends React.Component {
    render() {
        return (
        <div className="toolbar">
            <form method="GET" action="/room/random" className="toolbar__form">
                <input type="submit" className="toolbar_button" value="Connect"/>
            </form>
            <form method="POST" action="/room" className="toolbar__form">
                <input type="submit" className="toolbar__button" value="Create"/>
            </form>
        </div>);
    }
}

ReactDOM.render(<App />, document.querySelector('.__react-root'));