import React from 'react';

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

        this.props.socket.emit('user_joined_lobby');

        this.props.socket.on('room_list_updated', (id, room) => {
            if (Object.entries(room.viewers).length == 0) {
                let copy = this.state.roomList;
                delete copy[id];
                this.setState({
                    roomList: copy
                });
            }
            else {
                this.setState({
                    roomList: {
                        ...this.state.roomList,
                        [id]: room
                    }
                });
            }
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
                                <span>{Object.entries(room.viewers).length}</span>
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
                <div className="lobby__navbar" style={{background: 'black'}}>
                    <form method="POST" action="/room" className="lobby__navbar__create-btn">
                        <input type="submit" className="toolbar__button" value="Создать новую комнату"/>
                    </form>
                    <a href="/room/random" className="connect-btn">Подключиться к случайной</a>
                </div>
                <RoomMenu socket={this.props.socket}/>
            </div>
        )
    }
}
