import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ProductList from "./components/ProductList";
import AddProduct from "./components/AddProduct";
import UpdateProduct from "./components/UpdateProduct";
import DeleteProduct from "./components/DeleteProduct";

const App = () => {
  return (
    <Router>
      <div className="container">
        <header>
          <h1>Product Management</h1>
          <nav>
            <Link to="/">Home</Link>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<ProductList />} />
          <Route path="/add" element={<AddProduct />} />
          <Route path="/update/:id" element={<UpdateProduct />} />
          <Route path="/delete/:id" element={<DeleteProduct />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
