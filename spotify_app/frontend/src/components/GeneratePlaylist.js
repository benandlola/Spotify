import React, { useEffect, useState } from "react";
import { Button, Grid, Typography, Collapse, Alert, createTheme, ThemeProvider} from "@mui/material";
import { Link } from "react-router-dom";

export default function GeneratePlaylist() {
    const [details, setDetails] = useState({
        spotifyAuthenticated: false,
        topArtists: [],
        successMsg: "",
    });

    useEffect(() => {
        authenticateSpotify();
        fetch("/spotify/top-artists") 
        .then((response) => response.json())
        .then((data) => {
            setDetails({
                ...details,
                topArtists: data,
            });
        })
    }, []);

    const authenticateSpotify = () => {
        fetch("/spotify/is-authenticated")
        .then((response) => response.json())
        .then((data) => {
            setDetails((prevState) => ({
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

    const GenerateTopTracksPlaylist = (time_range) => {
        const requestOptions = {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ time_range: time_range })
        }
    
        fetch('/spotify/top-tracks-playlist', requestOptions);    
        fetch('/spotify/update-playlist', requestOptions)
        .then((response) => response.json())
        .then((data) => {
            setDetails((prevState) => ({
                ...prevState,
                successMsg: data + ' Playlist created!'
            }))
        });

    }

    const GenerateTopArtistPlaylist = (artist_id) => {
        const requestOptions = {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ artist_id : artist_id })
        }
    
        fetch('/spotify/top-artist-playlist', requestOptions);
        fetch('/spotify/update-playlist', requestOptions)
        .then((response) => response.json())
        .then((data) => {
            setDetails((prevState) => ({
                ...prevState,
                successMsg: data + ' Playlist created!'
            }))
        });
    }


    //THEMES
    function getRandomColor() {
        const randomColor = `rgb(${Math.floor(Math.random() * 256)}, ${Math.floor(
            Math.random() * 256
        )}, ${Math.floor(Math.random() * 256)})`;    
        return randomColor;
    }
      
    function TopArtistsButtons({ artist }) {
        const topArtistsTheme = createTheme({
            palette: {
              primary: {
                main: getRandomColor(), // Random background color
                contrastText: '#fff', // Text color
              },
            },
        });

        return (
            <ThemeProvider theme={topArtistsTheme}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => GenerateTopArtistPlaylist(artist.id)}
              >
                {artist.name}
              </Button>
            </ThemeProvider>
          );
        }



    return (
        <Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Collapse in={details.successMsg !== ""}>
                    <Alert severity="success" onClose={() => setDetails({...details, successMsg: ''})}>
                        {details.successMsg}
                    </Alert>
                </Collapse>
                <Typography variant="h3">
                    Playlist Generator
                </Typography>
                <Button variant="contained" color="primary" onClick={() => GenerateTopTracksPlaylist('short_term')}>
                    Recently Listened to Vibes
                </Button>
                <Button variant="contained" color="secondary" onClick={() => GenerateTopTracksPlaylist('medium_term')}>
                    Throwback Tracks 
                </Button>
                <Button variant="contained" color="primary" onClick={() => GenerateTopTracksPlaylist('long_term')}>
                    All Time Favourites
                </Button>
            </Grid>
            <Grid item xs={12} align="center">
                <Typography variant="h4">Your Top 10 Artists</Typography>
                <ul style={{listStyleType: 'none',  padding: 0}}>
                {details.topArtists.map((artist) => (
                    <li key={artist.id} style={{ margin:'10px'}}>
                     <TopArtistsButtons artist={artist} />
                    </li>
                ))}
                </ul>
            </Grid>
            <Grid item xs={12} align="center">
                <Button variant="contained" color="primary" to="/" component={Link}>
                    Back
                </Button>
            </Grid>
        </Grid>
    );
}