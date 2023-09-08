import React, { Component } from "react";
import { Button, Grid, Typography, TextField, FormHelperText, FormControl, Radio, RadioGroup, FormControlLabel } from "@mui/material";
import { Link } from "react-router-dom";

export default class RoomJoinPage extends Component {
    defaultVotes = 2
    constructor(props) {
        super(props);
    }
    render() {
        return (<Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Typography component="h4" variant="h4">
                    Create a Room
                </Typography>
            </Grid>   
        </Grid>);
    }
}