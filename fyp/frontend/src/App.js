import Chatbot from './Chatbot'
import './App.css';
import {Routes, Route} from 'react-router-dom';
import Home from './components/Home';
import About from './components/About';
import Create from './components/Create';
import MiniDrawer from './components/NavBar';
import Edit from './components/Edit';
import Delete from './components/Delete';
import CreatePortfolioAsset from './components/CreatePortfolioAsset';

function App() {
  return (
    <div className='App'>
      <MiniDrawer 
        content = {
          <Routes>
            <Route path='' element={<Home/>}/>
            <Route path='/about' element={<About/>}/>
            <Route path='/create' element={<Create/>}/>
            <Route path='/edit/:id' element={<Edit/>}/>
            <Route path='/delete/:id' element={<Delete/>}/>
            <Route path='/createPortfolioAsset' element={<CreatePortfolioAsset/>}/>
          </Routes>
        }
      />
    </div>
  );
}

export default App;
