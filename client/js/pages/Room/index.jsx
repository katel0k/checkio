import React from 'react';
// import CheckersUI from '../../components/CheckersUI';

function User(props) {
    return (
        <div className="game__user">
            <div className="game__user__info">
                <div className="game__user__info_name">User1</div>
                <div className="game__user__info_rate">
                    {/*  style="color: #000000;" */}
                    <div><i className="fa-solid fa-signal"></i></div> 
                    <div className="rate">1984</div>
                </div>

            </div>
            <div className="game__user__round">
                <img src="img/user_photo/user1.png" alt="" />
            </div>
        </div>
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

            <div className="game__play__content game__play__content_active">
                <div className="game__play__item">
                    <p>История ходов</p>
                </div>
            </div>
            <div className="game__play__content">
                <div className="game__play__item">
                    <p>Сообщения игроков</p>
                </div>
            </div>
        </div>
    );
}

export default class Room extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="container">
                <div className="game__wrapper">
                    <User/>
                    <div className="game__btns">
                        <button className="btn btn_game">Ничья</button>
                        <button className="btn btn_game">Поражение</button>
                    </div>
                    <GamePlay />
                    <User/>
                </div>
            </div>
        );
    }
}