import React from 'react';
import CheckersUI from '../../components/CheckersUI';

const { io } = require("socket.io-client");
const socket = io();

function User(props) {
    if (props.userInfo) {
        return (
            <div className="game__user">
                <div className="game__user__info">
                    <div className="game__user__info_name">{props.userInfo.nickname}</div>
                    <div className="game__user__info_rate">
                        <div><i className="fa-solid fa-signal"></i></div> 
                        <div className="rate">{props.userInfo.rating}</div>
                    </div>
    
                </div>
                <div className="game__user__round">
                    <img src="/client/img/user_photo/user1.png" alt="Ы" />
                </div>
            </div>
        );
    }
    else {
        return (
            <div className="game__user">
                Пользователь еще не подключился
            </div>
        )
    }   
}

function UserList(props) {
    return (
        <section className="guests">
            <div className="container">
                <div className="guests__wrapper">
                    <div className="guests__title">В комнате-</div>
                    {
                        Object.entries(props.userList).map(
                            ([id, {nickname}], i) => 
                            <div className="guests__item" key={i}>
                                <div className="guests__round">
                                    <img src="img/user_photo/user1.png" alt="S" />
                                </div>
                                <div className="guests__round__status"></div>
                                <div className="guests__descr">
                                    <div className="guests__descr-name">{nickname}</div>
                                </div>
                            </div>
                        )
                    }
                </div>
            </div>
        </section>
    );
}

function GamePlay(props) {
    return (
        <div className="game__play">
            <ul className="game__play__tabs">
                <li className="game__play__tab game__play__tab_active">
                    <div>Ходы</div>
                </li>
                <li className="game__play__tab">
                    <div>Чат</div>

                </li>
            </ul>
            <UserList userList={props.userList}/>
        </div>
    );
}

function GameSetter(props) {
    return (
        <div className="container">
            <div className="settings__wrapper">
                <div className="settings__users">
                    <div className="settings__user">
                        <div className="game__user__round">
                            <img src="img/user_photo/user1.png" alt="" />
                        </div>
                        <button className="btn btn_game" 
                            onClick={props.handleConnectBtnClick}>Подключиться</button>
                    </div>
                </div>
            </div>
        </div>
    );
}



const waiting_state = 'waiting';
const playing_state = 'playing';

export default class Room extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            viewers: {},
            state: waiting_state,
            messages: {},
            whitePlayer: undefined,
            blackPlayer: undefined,
            self: {
                id: undefined,
                color: undefined
            },
            game: undefined
        };
    }

    componentDidMount() {
        socket.on('player_joined', (viewers) => {
            this.setState({
                viewers: {
                    ...viewers,
                    ...this.state.viewers
                }
            });
        });

        socket.on('player_set', (player) => {
            this.setState({
                whitePlayer: player
            });
        });

        socket.on('game_started', (obj) => {
            console.log(obj);
            let color = undefined;
            if (this.state.self.id == obj.white_player.id)
                color = 'white'
            else if (this.state.self.id == obj.black_player.id)
                color = 'black';
            this.setState({
                state: playing_state,
                whitePlayer: obj.white_player,
                blackPlayer: obj.black_player,
                self: {
                    ...this.state.self,
                    color
                },
                game: obj.game
            });
        });

        // window.onbeforeunload = function () {
        //     socket.emit('client_disconnecting', 
        //         {
        //             room_id: this.state.roomId,
        //             user_id: this.state.self.id
        //         }
        //         );
        // }

        fetch(new URL('info', location.href))
            .then(response => response.json())
            .then(obj => {
                let color;
                if (obj.state == playing_state) {
                    if (obj.user.id == obj.white_player.id)
                        color = 'white'
                    else if (obj.user.id == obj.black_player.id)
                        color = 'black';
                }
                this.setState({
                    roomId: obj.id,
                    state: obj.state,
                    whitePlayer: obj.white_player,
                    blackPlayer: obj.black_player,
                    viewers: obj.viewers,
                    self: {
                        id: obj.user.id,
                        color
                    }
                });
                return obj;
            })
            .then(({id}) => {
                socket.emit('join', id);
            });
    }

    handleConnectBtnClick() {
        socket.emit('join_game', this.state.roomId);
    }

    render() {
        return (
            <div className="container">
                <div className="game__wrapper">
                    <User userInfo={this.state.whitePlayer}/>
                    <GamePlay userList={this.state.viewers}/>
                    <User userInfo={this.state.blackPlayer}/>
                    {
                        this.state.state == waiting_state ?
                        <GameSetter handleConnectBtnClick={this.handleConnectBtnClick.bind(this)} /> :
                        <CheckersUI playerColor={this.state.self.color} roomId={this.state.roomId} socket={socket}/>
                    }
                </div>
            </div>
        );
    }
}