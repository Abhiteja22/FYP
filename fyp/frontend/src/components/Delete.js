
import {React, useEffect, useState} from "react";
import { Box, Typography, Button } from "@mui/material";
import AxiosInstance from "./Axios";
import { useNavigate, useParams } from "react-router-dom";

const Delete = () => {
    const MyParam = useParams()
    const myId = MyParam.id

    const [myData, setMydata] = useState([])
    const [loading, setLoading] = useState(true)

    const GetData = () => {
        AxiosInstance.get(`portfolio/${myId}`).then((res) => {
            setMydata(res.data)
            console.log(res.data)
            setLoading(false)
        })
    }

    useEffect(() => {
        GetData();
    },[])

    const navigate = useNavigate()
    const submission = (data) => {
        AxiosInstance.delete(`portfolio/${myId}/`)
        .then((res) => {
            navigate(`/`)
        })
    }
    return (
        <div>
            { loading ? <p>Loading data...</p> :
            <div>
            <Box sx={{display:'flex', width:'100%', backgroundColor:'#00003f', marginBottom:'10px'}}>
                <Typography sx={{marginLeft:'20px', color:'#fff'}}>
                    Delete Portfolio: {myData.name}
                </Typography>
            </Box>

            <Box sx={{display:'flex', width:'100%', boxShadow:3, padding:4, flexDirection:'column'}}>
                <Box sx={{display:'flex', justifyContent:'start', marginBottom: '40px'}}>
                    Are you sure that you want to delete portfolio: {myData.name}
                </Box>
                <Box sx={{display:'flex', justifyContent:'start', width:'30%'}}>
                    <Button variant='contained' color='error' onClick={submission}>
                        Delete the project
                    </Button>
                </Box>
            </Box>
            </div>
            }
        </div>
    )
}

export default Delete