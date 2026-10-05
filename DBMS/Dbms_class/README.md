# Product Management System (React + Spring Boot + MySQL)

A full-stack CRUD application for managing products with a Spring Boot REST API backend and a Vite + React frontend.

---

## 📁 Project Structure

```text
Dbms_class/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── components/
│       │   ├── ProductList.jsx
│       │   ├── AddProduct.jsx
│       │   ├── UpdateProduct.jsx
│       │   └── DeleteProduct.jsx
│       └── services/
│           └── productService.jsx
└── backend/
    ├── pom.xml
    └── src/
        └── main/
            ├── java/com/klu/
            │   ├── Week9Co3Application.java
            │   ├── controller/
            │   │   └── ProductController.java
            │   ├── model/
            │   │   └── Product.java
            │   ├── repository/
            │   │   └── ProductRepository.java
            │   └── service/
            │       ├── ProductService.java
            │       └── ProductServiceImpl.java
            └── resources/
                └── application.properties
```

---

## 🚀 How to Run the Application

### 1. Database Setup (MySQL)
Ensure your MySQL server is running on port `3306`:
- Database name: `kluh` (will be automatically created if not present)
- Username: `root`
- Password: `root`

*(You can modify credentials in `backend/src/main/resources/application.properties` if your MySQL password differs)*

---

### 2. Run the Backend (Spring Boot)
Open a terminal in the `backend` folder:

```bash
cd backend
mvn spring-boot:run
```
Or run `Week9Co3Application.java` directly in VS Code / IntelliJ IDEA / Eclipse.
The backend API will start on: **`http://localhost:8080`**

#### REST Endpoints:
- `GET /api/products` - Get all products
- `GET /api/products/{id}` - Get product by ID
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product by ID
- `DELETE /api/products/{id}` - Delete product by ID

---

### 3. Run the Frontend (React + Vite)
Open a terminal in the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at: **`http://localhost:5173`**

---

## 🛠️ Tech Stack
- **Frontend**: React, Vite, React Router DOM, Axios
- **Backend**: Spring Boot 3, Spring Data JPA, Hibernate, Lombok
- **Database**: MySQL
