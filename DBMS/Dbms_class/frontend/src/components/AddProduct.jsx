import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { addProduct } from '../services/productService';

const AddProduct = () => {
  const navigate = useNavigate();
  const [product, setProduct] = useState({ name: '', description: '', price: '', quantity: '' });

  const handleChange = (e) => {
    setProduct({ ...product, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    addProduct(product)
      .then(() => {
        alert("Product added successfully!");
        navigate("/");
      })
      .catch((error) => {
        console.error("Error adding product:", error);
        alert("Failed to add product");
      });
  };

  return (
    <div>
      <h2>Add Product</h2>
      <form onSubmit={handleSubmit}>
        <label>Name:</label>
        <input type="text" name="name" placeholder="Name" value={product.name} onChange={handleChange} required />
        
        <label>Description:</label>
        <input type="text" name="description" placeholder="Description" value={product.description} onChange={handleChange} />
        
        <label>Price:</label>
        <input type="number" step="0.01" name="price" placeholder="Price" value={product.price} onChange={handleChange} required />
        
        <label>Quantity:</label>
        <input type="number" name="quantity" placeholder="Quantity" value={product.quantity} onChange={handleChange} required />
        
        <div className="form-actions">
          <button type="submit" className="btn btn-primary">Add Product</button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/')}>Cancel</button>
        </div>
      </form>
    </div>
  );
};

export default AddProduct;
