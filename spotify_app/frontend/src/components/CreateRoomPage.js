import React, { useState } from "react";
import {
    Button,
    Grid,
    Typography,
    TextField,
    FormHelperText,
    FormControl,
    Radio,
    RadioGroup,
    FormControlLabel,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

function CreateRoomPage() {
    // Set the default number of votes
    const defaultVotes = 2;
    // Initialize the navigation function for redirecting to other pages
    const navigate = useNavigate();

    // Define the state for room data using useState hook
    const [roomData, setRoomData] = useState({
        guestCanPause: true,
        votesToSkip: defaultVotes,
    });

    // Event handler for changing the number of votes
    const handleVotesChange = (e) => {
        setRoomData({
            ...roomData,
            votesToSkip: e.target.value,
        });
    };

    // Event handler for changing the guest control of playback state
    const handleGuestCanPauseChange = (e) => {
        setRoomData({
            ...roomData,
            guestCanPause: e.target.value === "true",
        });
    };

    // Event handler for creating a room
    const handleRoomButtonPressed = () => {
        // Define request options for the API call
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                votes_to_skip: roomData.votesToSkip,
                guest_can_pause: roomData.guestCanPause,
            }),
        };

        // Make an API call to create the room
        fetch("/api/create-room", requestOptions)
            .then((response) => response.json())
            .then((data) => {
                // Log the API response and navigate to the created room
                navigate(`/room/${data.code}`);
            });
    };

    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Typography component="h4" variant="h4">
                    Create a Room
                </Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl component="fieldset">
                    <FormHelperText>
                        <div align="center">Guest Control of Playback State</div>
                    </FormHelperText>
                    <RadioGroup
                        row
                        value={roomData.guestCanPause.toString()}
                        onChange={handleGuestCanPauseChange}
                    >
                        <FormControlLabel
                            value="true"
                            control={<Radio color="primary" />}
                            label="Play/Pause"
                        />
                        <FormControlLabel
                            value="false"
                            control={<Radio color="secondary" />}
                            label="No Control"
                        />
                    </RadioGroup>
                </FormControl>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl>
                    <TextField
                        required={true}
                        type="number"
                        onChange={handleVotesChange}
                        value={roomData.votesToSkip}
                        inputProps={{ min: 1, style: { textAlign: "center" } }}
                    />
                    <FormHelperText>
                        <div align="center">Votes Required To Skip Song</div>
                    </FormHelperText>
                </FormControl>
            </Grid>
            <Grid item xs={12} align="center">
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={handleRoomButtonPressed}
                >
                    Create a Room
                </Button>
            </Grid>
            <Grid item xs={12} align="center">
                <Button
                    color="primary"
                    variant="contained"
                    component={Link}
                    to="/"
                >
                    Back
                </Button>
            </Grid>
        </Grid>
    );
}

export default CreateRoomPage;