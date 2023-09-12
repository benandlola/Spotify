import React, { useState } from "react";
import { TextField, Button, Grid, Typography } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

export default function RoomJoinPage() {
  // Define state variables for room code and error message
  const [roomCode, setRoomCode] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate(); // Initialize the navigation function for redirecting to other pages

  // Event handler for changing the room code input field
  const handleTextFieldChange = (e) => {
    setRoomCode(e.target.value);
  };

  // Event handler for joining a room
  const roomButtonPressed = () => {
    // Define request options for the API call
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: roomCode,
      }),
    };

    // Make an API call to join the room
    fetch("/api/join-room", requestOptions)
      .then((response) => {
        if (response.ok) {
          // If the response is successful, navigate to the room
          navigate(`/room/${roomCode}`);
        } else {
          // If the response is not successful, set an error message
          setError("Room not found.");
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography variant="h4" component="h4">
          Join a Room
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <TextField
          error={error}
          label="Code"
          placeholder="Enter a Room Code"
          value={roomCode}
          helperText={error}
          variant="outlined"
          onChange={handleTextFieldChange}
        />
      </Grid>
      <Grid item xs={12} align="center">
        <Button
          variant="contained"
          color="secondary"
          onClick={roomButtonPressed}
        >
          Enter Room
        </Button>
      </Grid>
      <Grid item xs={12} align="center">
        <Button variant="contained" color="primary" to="/" component={Link}>
          Back
        </Button>
      </Grid>
    </Grid>
  );
}