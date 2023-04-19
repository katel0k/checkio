import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Lobby from './pages/Lobby';

export default function App() {
    return (
        <div className="wrapper">
            <Routes>
                <Route path="/" element={<Lobby />}/>
            </Routes>
        </div>
    );
}