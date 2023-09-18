import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Grid, Button, Typography } from '@mui/material';
import CreateRoomPage from "./CreateRoomPage";
import MusicPlayer from "./MusicPlayer";

export default function Room(props) {
    // Access the 'roomCode' parameter from the URL
    const { roomCode } = useParams();
    const navigate = useNavigate(); // Initialize the navigate function 

    // Define state to store room details and initialize with default values
    const [roomDetails, setRoomDetails] = useState({
        votesToSkip: 1,
        guestCanPause: false,
        isHost: false,
        showSettings: false,
        spotifyAuthenticated: false,
        song: {}
    });

    // Define the fetchRoomDetails function
    const fetchRoomDetails = () => {
        // Fetch room details from the API based on the 'roomCode'
        fetch("/api/get-room" + "?code=" + roomCode)
        .then((response) => {
            if (!response.ok) {
                props.leaveRoomCallback();
                navigate("/");
            }
            return response.json();
        })
        .then((data) => {
            // Update the state with the retrieved room details
            setRoomDetails((prevState) => ({
                ...prevState,
                votesToSkip: data.votes_to_skip,
                guestCanPause: data.guest_can_pause,
                isHost: data.is_host,
            }));
            if (roomDetails.isHost) {
                authenticateSpotify();
            }
        });
    };

    // Use the fetchRoomDetails function in your useEffect
    useEffect(() => {
        fetchRoomDetails();
        getCurrentSong();
        const interval = setInterval(getCurrentSong, 1000);
        return () => {
            clearInterval(interval);
        }
    }, [roomCode]);

    const authenticateSpotify = () => {
        fetch("/spotify/is-authenticated")
        .then((response) => response.json())
        .then((data) => {
            setRoomDetails((prevState) => ({
                ...prevState,
                spotifyAuthenticated: data.status,
            }));
            if (!data.status) {
                fetch("/spotify/get-auth-url")
                .then((response) => response.json())
                .then((data) => {
                    window.location.replace(data.url);
                });
            }
        });
    }

    const getCurrentSong = () => {
        fetch("/spotify/current-song")
        .then((response) => {
            if (!response.ok) {
                return {};
            } else {
                return response.json();
            }
        })
        .then((data) => {
            setRoomDetails((prevState) => ({
                ...prevState,
                song: data,
            }));
        });      
    }

    // Leave the room
    const leaveButtonPressed = () => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"}, 
        }
        fetch('/api/leave-room', requestOptions).then((_response) => {
            props.leaveRoomCallback();
            navigate("/");
        });
    }

    const updateShowSettings = (value) => {
        setRoomDetails({ ...roomDetails, showSettings: value });
    }

    const renderSettingsButton = () => {
        return (
            <Grid item xs={12} align="center">
                <Button variant="contained" color="secondary" onClick={() => updateShowSettings(true)}>
                    Settings
                </Button>
            </Grid>
        );
    }

    const renderSettings = () => {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <CreateRoomPage 
                        update={true}
                        votesToSkip={roomDetails.votesToSkip}
                        guestCanPause={roomDetails.guestCanPause}
                        roomCode={roomCode}
                        updateCallback={fetchRoomDetails}
                    />
                </Grid>
                <Grid item xs={12} align="center">
                    <Button variant="contained" color="primary" onClick={() => updateShowSettings(false)}>
                        Close
                    </Button>
                </Grid>
            </Grid>
        );
    
    }
    if (roomDetails.showSettings) {
        return renderSettings();
    }
    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Typography variant="h4" component="h4">
                    Code: {roomCode}
                </Typography>
            </Grid>
            <MusicPlayer {...roomDetails.song} />
            {roomDetails.isHost ? renderSettingsButton() : null}
            <Grid item xs={12} align="center">
                <Button variant="contained" color="primary" onClick={leaveButtonPressed}>
                    Leave Room
                </Button>
            </Grid>
        </Grid>
    );
}