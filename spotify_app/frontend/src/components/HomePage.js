import React, { useEffect, useState } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import { Grid, Button, ButtonGroup, Typography } from "@mui/material";
import { BrowserRouter as Router, Routes, Route, Link, Navigate} from "react-router-dom";

function HomePage() {
    // State to store the room code
    const [roomCode, setRoomCode] = useState(null);
 
    useEffect(() => {
      // Fetch the user's room data when the component mounts
      fetch("/api/user-in-room")
        .then((response) => response.json())
        .then((data) => {
          // Set the room code in the state
          setRoomCode(data.code);
        });
    }, []);
    
    // Function to render the home page content
    const renderHomePage = () => {
        return (
        <Grid container spacing={3}>
            <Grid item xs={12} align="center">
            <Typography variant="h3" compact="h3">
                House Party
            </Typography>
            </Grid>
            <Grid item xs={12} align="center">
            <ButtonGroup disableElevation variant="contained" color="secondary">
                <Button color="secondary" to="/join" component={Link}>
                Join a Room
                </Button>
                <Button color="primary" to="/create" component={Link}>
                Create a Room
                </Button>
            </ButtonGroup>
            </Grid>
        </Grid>
        );
    }
  
    const clearRoomCode = () => {
      setRoomCode(null);
    }

    return (
      <Router>
        <Routes>
          <Route path="/join" element={<RoomJoinPage/>}/>
          <Route path="/create" element={<CreateRoomPage/>}/>
          <Route path="/room/:roomCode" 
            element={<Room leaveRoomCallback={clearRoomCode} />}
          />
          <Route
            path="/"
            element={roomCode ? <Navigate to={`/room/${roomCode}`} /> : renderHomePage()}
          />
        </Routes>
      </Router>
    );
}

export default HomePage;