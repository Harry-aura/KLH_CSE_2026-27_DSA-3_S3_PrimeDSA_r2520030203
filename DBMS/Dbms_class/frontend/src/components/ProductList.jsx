import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAllProducts, deleteProduct } from '../services/productService';

const ProductList = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = () => {
    getAllProducts()
      .then(response => {
        setProducts(response.data);
      })
      .catch(error => {
        console.error("Error fetching products:", error);
      });
  };

  const handleDelete = (id) => {
    deleteProduct(id).then(() => {
      setProducts(products.filter(product => product.id !== id));
    }).catch(error => {
      console.error("Error deleting product:", error);
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2>Product List</h2>
        <Link to="/add" className="btn btn-primary">+ Add Product</Link>
      </div>
      {products.length === 0 ? (
        <p style={{ color: '#6b7280' }}>No products found. Click "Add Product" to create one.</p>
      ) : (
        <ul>
          {products.map(product => (
            <li key={product.id} className="product-item">
              <div className="product-info">
                <span className="product-name">{product.name}</span>
                {product.description && <span className="product-desc">{product.description}</span>}
                <span className="product-price">${product.price} &bull; Qty: {product.quantity}</span>
              </div>
              <div className="btn-group">
                <Link to={`/update/${product.id}`} className="btn btn-edit">Edit</Link>
                <Link to={`/delete/${product.id}`} className="btn btn-delete">Delete</Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ProductList;
