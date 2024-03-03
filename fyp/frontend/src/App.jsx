import './App.css';
import { createTheme, colors, ThemeProvider, CssBaseline } from '@mui/material';
import {Routes, Route, useLocation} from 'react-router-dom';
import Home from './components/Home';
import About from './components/About';
import Create from './components/Create';
import MiniDrawer from './components/NavBar';
import Edit from './components/Edit';
import Delete from './components/Delete';
import CreatePortfolioAsset from './components/CreatePortfolioAsset';
import Chat from './components/Chat';
import Interact from './components/Interact';
import CreateChat from './components/CreateChat';
import EditChat from './components/EditChat';
import Login from './components/Login';
import Register from './components/Register';
import { Palette } from '@mui/icons-material';

const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // Light mode palette
          background: {
            default: '#f5f5ff',
          },
          primary: {
            main: '#104ec1',
          },
          secondary: {
            main: '#8b98e9',
            light: '#a2aced'
          },
        }
      : {
          // Dark mode palette
          background: {
            default: '#00000e',
          },
          primary: {
            main: '#3e7cef',
          },
          secondary: {
            main: '#162374',
            dark: '#0f1851'
          },
        }),
  },
});

// Create a theme instance based on the preferred mode
const theme = createTheme(getDesignTokens('dark'));

function App() {
  const location = useLocation()
  const noNavBar = location.pathname === "/register" || location.pathname === "/"
  return (
    <ThemeProvider theme={theme}>
    <CssBaseline />
    <div className='App'>
      {
        noNavBar ?
        <Routes>
          <Route path='/' element={<Login/>}/>
          <Route path='/register' element={<Register/>}/>
        </Routes>
        :
        <MiniDrawer 
        content = {
          <Routes>
            <Route path='/home' element={<Home/>}/>
            <Route path='/about' element={<About/>}/>
            <Route path='/create' element={<Create/>}/>
            <Route path='/edit/:id' element={<Edit/>}/>
            <Route path='/delete/:id' element={<Delete/>}/>
            <Route path='/createPortfolioAsset' element={<CreatePortfolioAsset/>}/>
            <Route path='/chat' element={<Chat/>}/>
            <Route path='/chat/create' element={<CreateChat/>}/>
            <Route path='/chat/edit/:id' element={<EditChat/>}/>
            <Route path='/chat/:chatId' element={<Interact/>}/>
          </Routes>
        }
      />
      }
      
    </div>
    </ThemeProvider>
  );
}

export default App;
