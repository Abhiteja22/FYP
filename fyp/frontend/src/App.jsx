import './App.css';
import { Routes, Route } from 'react-router-dom';
import Portfolios from './components/portfolio_components/Portfolios';
import About from './components/About';
import MiniDrawer from './components/NavBar';
import Chat from './components/Chat';
import Interact from './components/Interact';
import CreateChat from './components/CreateChat';
import EditChat from './components/EditChat';
import Login from './components/authentication/Login';
import Register from './components/authentication/Register';
import Home from './components/Home';
import MainWrapper from './layouts/MainWrapper';
import PrivateRoute from './layouts/PrivateRoute';
import Private from './components/Private';
import Logout from './components/authentication/Logout';
import Assets from './components/asset_components/Assets';
import Asset from './components/asset_components/Asset';
import Portfolio from './components/portfolio_components/Portfolio';
import OptimizePortfolio from './components/portfolio_components/OptimizePortfolio';

function App() {
  return (
      <MainWrapper>
        <Routes>
          <Route path='/login' element={<Login/>}/>
          <Route path='/register' element={<Register/>}/>
          <Route path='/logout' element={<Logout/>}/>

          {/* Redoing */}
          <Route path='/assets' element={<PrivateRoute> <MiniDrawer content= {<Assets/>} /> </PrivateRoute>}/>
          <Route path='/assets/:id' element={<PrivateRoute> <MiniDrawer content= {<Asset/>} /> </PrivateRoute>}/>
          <Route path='/portfolios' element={<PrivateRoute> <MiniDrawer content= {<Portfolios/>} /> </PrivateRoute>}/>
          <Route path='/portfolios/:id' element={<PrivateRoute> <MiniDrawer content= {<Portfolio/>} /> </PrivateRoute>}/>
          <Route path='/optimize/:id' element={<PrivateRoute> <MiniDrawer content= {<OptimizePortfolio/>} /> </PrivateRoute>}/>
          {/* Previous Routes */}
          <Route path='/private' element={<PrivateRoute> <MiniDrawer content= {<Private/>} /> </PrivateRoute>}/>
          <Route path="/" element={<PrivateRoute> <MiniDrawer content= {<Home/>} /> </PrivateRoute>} />
          <Route path='/about' element={<PrivateRoute> <MiniDrawer content= {<About/>} /> </PrivateRoute>}/>
          
          <Route path='/chat' element={<PrivateRoute> <MiniDrawer content= {<Chat/>} /> </PrivateRoute>}/>
          <Route path='/chat/create' element={<PrivateRoute> <MiniDrawer content= {<CreateChat/>} /> </PrivateRoute>}/>
          <Route path='/chat/edit/:id' element={<PrivateRoute> <MiniDrawer content= {<EditChat/>} /> </PrivateRoute>}/>
          <Route path='/chat/:chatId' element={<PrivateRoute> <MiniDrawer content= {<Interact/>} /> </PrivateRoute>}/>
          
        </Routes>
      </MainWrapper>
  );
}

export default App;
