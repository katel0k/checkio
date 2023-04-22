import React from 'react';
import {Link} from 'react-router-dom';

import './Lobby.sass';

import { io } from 'socket.io-client';
const socket = io();

class RoomMenu extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            roomList: {}
        };
    }

    componentDidMount() {
        fetch(new URL('room', location.href)).then(response => response.json())
        .then(obj => {
            this.setState({
                roomList: obj.room_list
            });
        });

        socket.on('room_list_updated', (id, newState, newPlayersAmount) => {
            this.setState({
                ...this.state.roomList,
                [id]: {
                    state: newState,
                    playersAmount: newPlayersAmount
                }
            });
        });
    }

    render() {
        return (
            <div className="room-menu">
                {
                    Object.entries(this.state.roomList).map(
                        ([room_id, room]) =>
                            <div className="room-menu__entry" key={room_id}>
                                <span>{room_id}</span>
                                <span>{room.state}</span>
                                <span>{room.playersAmount}</span>
                                <a href={"/room/" + room_id} className="connect-btn">Подключиться</a>
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