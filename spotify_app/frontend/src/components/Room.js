import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function Room() {
    // Access the 'roomCode' parameter from the URL
    const { roomCode } = useParams();

    // Define state to store room details and initialize with default values
    const [roomDetails, setRoomDetails] = useState({
        votesToSkip: 2,
        guestCanPause: false,
        isHost: false,
    });

    // Use the useEffect hook to fetch room details when the component mounts or 'roomCode' changes
    useEffect(() => {
        // Fetch room details from the API based on the 'roomCode'
        fetch("/api/get-room" + "?code=" + roomCode)
        .then((response) => response.json())
        .then((data) => {
            // Update the state with the retrieved room details
            setRoomDetails({
            votesToSkip: data.votes_to_skip,
            guestCanPause: data.guest_can_pause,
            isHost: data.is_host,
            });
        });
    }, [roomCode]);

    return (
        <div className="center">
        <h3>{roomCode}</h3>
        <p>Votes: {roomDetails.votesToSkip}</p>
        <p>Guest Can Pause: {roomDetails.guestCanPause.toString()}</p>
        <p>Host: {roomDetails.isHost.toString()}</p>
        </div>
    );
}

export default Room;
