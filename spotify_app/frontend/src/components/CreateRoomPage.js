import React, { useState } from "react";
import { Button, Grid, Typography, TextField, FormHelperText, FormControl, Radio, RadioGroup, FormControlLabel, Collapse, Alert} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

export default function CreateRoomPage(props) {
    const defaultRoomData = {
        votesToSkip : 1,
        guestCanPause : true,
        update : false,
        roomCode : null,
        updateCallback : () => {},
        successMsg : "",
        errorMsg : "",
    };

    const navigate = useNavigate();
    // Define the state for room data using useState hook
    const [roomData, setRoomData] = useState({...defaultRoomData, ...props});

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

    // Event handler for updating a room
    const handleUpdateButtonPressed = () => {
        // Define request options for the API call
        const requestOptions = {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                votes_to_skip: roomData.votesToSkip,
                guest_can_pause: roomData.guestCanPause,
                code: roomData.roomCode,
            }),
        };

        // Make an API call to update the room
        fetch("/api/update-room", requestOptions)
        .then((response) => {    
            setRoomData({
                ...roomData,
                successMsg: response.ok ? 'Room updated successfully!' : '',
                errorMsg: response.ok ? '' : 'Error updating room.',
            });
            roomData.updateCallback();
        });   
    };

    const renderCreateButtons = () => {
        return(
            <Grid container spacing={1}>
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
    };

    const renderUpdateButtons = () => {
        return(
            <Grid item xs={12} align="center">
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={handleUpdateButtonPressed}
                >
                    Update Room
                </Button>
            </Grid>
        );
    }

    const title = roomData.update ? "Update Room" : "Create a Room";
    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Collapse in={roomData.errorMsg !== "" || roomData.successMsg !== ""}>
                    {roomData.successMsg !== "" ? (
                    <Alert severity="success" onClose={() => setRoomData({...roomData, successMsg: ''})}>
                        {roomData.successMsg}</Alert>
                    ) : (
                    <Alert severity="error" onClose={() => setRoomData({...roomData, errorMsg: ''})}>
                        {roomData.errorMsg}</Alert>)}
                </Collapse>
            </Grid>
            <Grid item xs={12} align="center">
                <Typography component="h4" variant="h4">
                   {title}
                </Typography>
            </Grid>
            <Grid item xs={12} align="center">
                <FormControl component="fieldset">
                    <FormHelperText component="div">
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
                    <FormHelperText component="div">
                        <div align="center">Votes Required To Skip Song</div>
                    </FormHelperText>
                </FormControl>
            </Grid>
           {roomData.update ? renderUpdateButtons() : renderCreateButtons()}
        </Grid>
    );
}