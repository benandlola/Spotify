import React from "react";
import { Grid, Typography, Card, LinearProgress, IconButton } from '@mui/material';
import { PlayArrow, SkipNext, Pause, SkipPrevious } from '@mui/icons-material';

function MusicPlayer(props) {
    return (
        <Card>
            <Grid container alignItems="center">
                <Grid item align="center" xs={4}>
                    <img src={props.image_url} height="100%" width="100%" />
                </Grid>
                <Grid item align="center" xs={8}>
                    <Typography component="h5" variant="h5">
                        {props.title}
                    </Typography>
                    <Typography color="textSecondary" variant="subtitle1">
                        {props.artist}
                    </Typography>
                    <div>
                        <IconButton>
                            <SkipPrevious />
                        </IconButton>
                        <IconButton>
                            {props.is_playing ? <Pause /> : <PlayArrow/>}
                        </IconButton>
                        <IconButton>
                            <SkipNext />
                        </IconButton>
                    </div>
                </Grid>
            </Grid>
            <LinearProgress variant="determinate" value={(props.time / props.duration) * 100}/>  
        </Card>
    );
}

export default MusicPlayer;