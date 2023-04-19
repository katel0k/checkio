import React from 'react';
import {Link} from 'react-router-dom';

class RoomMenu extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            roomList: []
        };
    }

    componentDidMount() {
        fetch(new URL('room', location.href)).then(response => response.json())
        .then(obj => {
            this.setState({
                roomList: obj.room_list
            });
        });
    }

    render() {
        return (
            <div className="room-menu">
                {
                    this.state.roomList.map(
                        (room, i) => 
                            <div className="room-menu__entry" key={i}>
                                <span>{room.index}</span>
                                <span>{room.state}</span>
                                <span>{room.playersAmount}</span>
                                <Link to={"/room/" + room.index}>Подключиться</Link>
                            </div>
                    )
                }
            </div>
        )
    }
}

export default class Lobby extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <div className="lobby__navbar">
                    <form method="POST" action="/room" className="lobby__navbar__create-btn">
                        <input type="submit" className="toolbar__button" value="Создать новую комнату"/>
                    </form>
                    <a href="/room/random" className="connect-btn">Подключиться к случайной</a>
                </div>
                <RoomMenu />
            </div>
        )
    }
}