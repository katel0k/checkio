import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Lobby from './pages/Lobby';
import Room from './pages/Room';
import User from './pages/User';

import { io } from 'socket.io-client';
const socket = io();

export default function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Lobby socket={socket}/>}/>
                <Route path="/index" element={<Lobby socket={socket}/>}/>
                <Route path="/room">
                    <Route path=":room_id"  element={<Room 
                        socket={socket}
                    />}/>
                </Route>
                <Route path="/user" element={<User />} />
            </Routes>
        </>
    );
}