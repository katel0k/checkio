import React from 'react';
import CheckersUI from '../../components/CheckersUI';

const { io } = require("socket.io-client");
const socket = io();

function User(props) {
    if (!props.userInfo) {
        return (
            <div className="user">
                Пользователь еще не подключился
            </div>
        )
    }
    return (
        <div className="user">
            <div className="user__round">
                <img src="img/user_photo/user1.png" alt="" />
            </div>
            <div className="user__info">
                <div className="user_name">{props.userInfo.nickname}</div>
                <div className="user_rate">
                    <div><i className="fa-solid fa-signal" style={{color: "#ffffff"}}></i></div>
                    <div className="rate">{props.userInfo.rating}</div>
                </div>
            </div>
            <div className="user__close">&times;</div>
            <div className={"user__color " + (props.color)}></div>
        </div>);
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
    <div className="settings__wrapper">
        <div className="settings__types__wrapper">
            <div className="settings__types">
                <div className="settings__types_group">
                    <input type="radio"/>
                    <label>Русские правила</label>
                </div>
                <div className="settings__types_group">
                    <input type="radio"/>
                    <label>Английские правила</label>
                </div>
                <div className="settings__types_group">
                    <input type="radio"/>
                    <label>Международные правила</label>
                </div>
                <div className="settings__types_group">
                    <input type="radio"/>
                    <label>Свои правила</label>
                </div>
            </div>


            <div className="settings__rules">
                <div className="settings__rules_group">
                    <input type="checkbox" />
                    <label>Белые ходят первые</label>
                </div>
                <div className="settings__rules_group">
                    <input type="checkbox" />
                    <label>Простая шашка может есть назад</label>
                </div>
                <div className="settings__rules_group">
                    <input type="checkbox" />
                    <label>Шашка может превращаться в двамку</label>
                </div>
                <div className="settings__rules_group">
                    <input type="checkbox" />
                    <label>Дамка может вставать на произвольное поле</label>
                </div>
                <div className="settings__rules_group">
                    <input type="checkbox" />
                    <label>Дамка может ходить на несколько полей</label>
                </div>
            </div>
        </div>

        <div className="settings__connect__wrapper">
            <button className="btn btn_game" onClick={props.handleConnectBtnClick}>Подключиться</button>
            <button className="btn btn_game" onClick={props.handleConnectBtnClick}>Подключиться</button>
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
            <section className="waiting">
                <div className="container">
                    <div className="waiting__container">
                        <div className="users__wrapper">
                            <User userInfo={this.state.whitePlayer} color='white'/>
                            <GamePlay userList={this.state.viewers}/>
                            <User userInfo={this.state.blackPlayer} color='black'/>
                        </div>
                        {
                            this.state.state == waiting_state ?
                            <GameSetter handleConnectBtnClick={this.handleConnectBtnClick.bind(this)} /> :
                            <CheckersUI playerColor={this.state.self.color} roomId={this.state.roomId} socket={socket}/>
                        }
                    </div>
                </div>
            </section>
        );
    }
}