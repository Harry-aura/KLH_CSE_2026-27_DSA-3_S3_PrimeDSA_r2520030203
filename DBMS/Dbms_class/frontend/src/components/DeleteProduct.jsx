import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { deleteProduct } from "../services/productService";

const DeleteProduct = () => {
  const { id } = useParams(); // Get product ID from URL params
  const navigate = useNavigate();

  const handleDelete = async () => {
    try {
      await deleteProduct(id);
      alert("Product deleted successfully!");
      navigate("/"); // Redirect to product list
    } catch (error) {
      console.error("Error deleting product:", error);
      alert("Failed to delete product");
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Are you sure you want to delete this product?</h2>
      <p style={{ color: "#6b7280", margin: "12px 0 24px" }}>Product ID: <strong>{id}</strong></p>
      <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
        <button onClick={handleDelete} className="btn btn-danger">Yes, Delete</button>
        <button onClick={() => navigate("/")} className="btn btn-secondary">Cancel</button>
      </div>
    </div>
  );
};

export default DeleteProduct;
