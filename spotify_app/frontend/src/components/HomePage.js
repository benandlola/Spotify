import React from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import { BrowserRouter as Router, Routes, Route, Link, Redirect } from "react-router-dom";

function HomePage() {
    return (
        <Router>
            <Routes>
                <Route path="/join" element={<RoomJoinPage />} />
                <Route path="/create" element={<CreateRoomPage />} />
                <Route path="/room/:roomCode" element={<Room />} />
                <Route path="/" element={<p>This is the Home Page</p>} />
            </Routes>
        </Router>
    );
}

export default HomePage;