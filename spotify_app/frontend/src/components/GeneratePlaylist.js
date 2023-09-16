import React, { useEffect, useState } from "react";
import { Button, Grid,} from "@mui/material";
import { Link } from "react-router-dom";

export default function GeneratePlaylist() {
    const [roomDetails, setRoomDetails] = useState({
        spotifyAuthenticated: false,
    });

    useEffect(() => {
        authenticateSpotify();
    }, []);

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

    return (
        <Grid item xs={12} align="center">
            <Button variant="contained" color="primary" to="/" component={Link}>
            Back
            </Button>
      </Grid>
    );
}