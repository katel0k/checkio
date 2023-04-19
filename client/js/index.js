// import React from 'react';
// import ReactDOM from 'react-dom';
// const { io } = require("socket.io-client");
// const socket = io();

// const url = new URL("http://localhost:5000/");

// class App extends React.Component {
//     constructor (props) {
//         super(props);
//     }
//     render () {
//         return (<div className="main-page-wrapper">
//             <div className="main-page">
//                 <div className="toolbar-wrapper">
//                     <Toolbar />
//                 </div>
//                 <div className="rooms-wrapper">
//                     <Rooms />
//                 </div>
//             </div>
//         </div>);
//     }
// }

// class Rooms extends React.Component {
//     constructor (props) {
//         super(props);
//         this.state = {
//             room_list: []
//         };
//     }
//     componentDidMount () {
//         fetch(new URL('room', url)).then(response => response.json())
//         .then(obj => {
//             // console.log(obj);
//             // console.log(this);
//             // console.log('obj', obj);
            
//             this.setState({
//                 room_list: obj.room_list
//             });
//         });
//         // socket.on('room_list_changed', (...args) => {

//         // });
//     }
//     render() {
//         console.log(this.state);
//         return (<div className="rooms">
//                     {
//                         this.state.room_list.map((a, i) => 
//                             <div className="room" key={i} >
//                                 <span>Room #{a}</span>
//                                 <ConnectBtn address={`/room/${a}`}/>
//                             </div>
//                         )
//                     }
//                 </div>);
//     }
// }

// function ConnectBtn (props) {
//     return (
//         <form method="GET" action={props.address} className="toolbar__form">
//             <input type="submit" className="toolbar_button" value="Connect"/>
//         </form>
//     );
// }

// class Toolbar extends React.Component {
//     render() {
//         return (
//         <div className="toolbar">
//             <ConnectBtn address="/room/random"/>
//             <form method="POST" action="/room" className="toolbar__form">
//                 <input type="submit" className="toolbar__button" value="Create"/>
//             </form>
//         </div>);
//     }
// }



import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter as Router} from 'react-router-dom';
import App from './App';

ReactDOM.render(
    <React.StrictMode>
        <Router>
            <App />
        </Router>
    </React.StrictMode>

    , document.querySelector('.__react-root'));