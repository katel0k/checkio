import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Lobby from './pages/Lobby';
import Room from './pages/Room';

export default function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Lobby />}/>
                <Route path="/index" element={<Lobby />}/>
                <Route path="/room">
                    <Route path=":room_id"  element={<Room 
                        
                    />}/>
                </Route>
            </Routes>
        </>
    );
}