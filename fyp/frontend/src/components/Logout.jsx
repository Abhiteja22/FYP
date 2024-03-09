import { useEffect } from 'react';
import Login from './Login';
import { logout } from '../utils/auth';

const Logout = () => {
    useEffect(() => {
        logout();
    }, []);
    return <Login/>;
};

export default Logout;