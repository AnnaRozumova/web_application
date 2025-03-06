document.addEventListener("DOMContentLoaded", function() {

    // Function to clear all result sections
    function clearAllResults() {
        document.getElementById("customerList").innerHTML = "";
        document.getElementById("listProducts").innerHTML = "";
        document.getElementById("listPurchases").innerHTML = "";
        document.getElementById("totalPrice").innerHTML = "";

        // Clear add-product-form inputs
        let productInputs = ["product_name", "price", "available_amount"];
        productInputs.forEach(field => {
            let input = document.querySelector(`input[name='${field}']`);
            if (input) input.value = "";
        });

        // Hide product message div
        let messageDiv = document.getElementById("product-message");
        if (messageDiv) {
            messageDiv.style.display = "none";
            messageDiv.innerHTML = "";
        }
    }

    // Attach event listeners to all buttons to clear results
    let buttons = document.querySelectorAll("button");
    buttons.forEach(button => {
        button.addEventListener("click", function(event) {
            if (event.target.id !== "searchCustomersButton") {  // Skip clearing on search button
                clearAllResults();
            }
        });
    });

    // Fetch customers functionality
    document.getElementById("fetchCustomers").addEventListener("click", function() {
        clearAllResults();
        fetch("/all-customers")
            .then(response => response.json())
            .then(data => {
                let customerList = document.getElementById("customerList");
                if (data.length > 0) {
                    data.forEach(customer => {
                        let customerItem = document.createElement("p");
                        customerItem.textContent = `Name: ${customer.name} ${customer.surname}, Email: ${customer.email}`;
                        customerList.appendChild(customerItem);
                    });
                } else {
                    customerList.innerHTML = "<p>No customers found.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching customers:", error);
                document.getElementById("customerList").innerHTML = "<p>Error retrieving data.</p>";
            });
    });

    // Fetch products functionality
    document.getElementById("fetchProducts").addEventListener("click", function() {
        clearAllResults();
        fetch("/all-products")
            .then(response => response.json())
            .then(data => {
                let productList = document.getElementById("listProducts");
                if (data.length > 0) {
                    data.forEach(product => {
                        let productItem = document.createElement("p");
                        productItem.textContent = `Product: ${product.product_name}, Price: ${product.price}, Amount: ${product.available_amount}`;
                        productList.appendChild(productItem);
                    });
                } else {
                    productList.innerHTML = "<p>No products found.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching products:", error);
                document.getElementById("listProducts").innerHTML = "<p>Error retrieving products.</p>";
            });
    });

    // Fetch purchases functionality
    document.getElementById("fetchPurchases").addEventListener("click", function() {
        clearAllResults();
        fetch("/all-purchases")
            .then(response => response.json())
            .then(data => {
                let purchaseList = document.getElementById("listPurchases");
                if (data.length > 0) {
                    data.forEach(purchase => {
                        let productDetails = purchase.products.map(p => `${p.product_name} (x${p.amount})`).join(", ");
                        let purchaseItem = document.createElement("p");
                        purchaseItem.textContent = `Purchase ID: ${purchase.purchase_id}, Total price: ${purchase.total_price}, Products: ${productDetails}`;
                        purchaseList.appendChild(purchaseItem);
                    });
                } else {
                    purchaseList.innerHTML = "<p>No purchases found.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching purchases:", error);
                document.getElementById("listPurchases").innerHTML = "<p>Error retrieving purchases.</p>";
            });
    });

    // Fetch total purchase price
    document.getElementById("fetchTotal").addEventListener("click", function() {
        clearAllResults();
        fetch("/all-purchases-price")
            .then(response => response.json())
            .then(data => {
                let totalPriceElement = document.getElementById("totalPrice");
                if (data.total_price !== undefined) {
                    totalPriceElement.textContent = `Total Price: $${data.total_price}`;
                } else {
                    totalPriceElement.innerHTML = "<p>No purchase data available.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching total purchase price:", error);
                document.getElementById("totalPrice").innerHTML = "<p>Error retrieving total price.</p>";
            });
    });

    // Handle search customers form submission
    document.getElementById("search-customers-form").addEventListener("submit", function(event) {
        event.preventDefault(); 

        let name = document.querySelector("input[name='name']").value.trim();
        let surname = document.querySelector("input[name='surname']").value.trim();
        let email = document.querySelector("input[name='email']").value.trim();
        let resultsDiv = document.querySelector("#search-results blockquote");

        // Debugging
        console.log("Searching for:", { name, surname, email });

        resultsDiv.innerHTML = "<p>Searching...</p>";

        let searchParams = new URLSearchParams();
        if (name) searchParams.append("name", name);
        if (surname) searchParams.append("surname", surname);
        if (email) searchParams.append("email", email);

        fetch(`/search-customers?${searchParams.toString()}`)
            .then(response => response.json())
            .then(data => {
                console.log("Search response:", data);

                resultsDiv.innerHTML = "";

                if (data.error) {
                    resultsDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
                } else {
                    let customerInfo = `<p><strong>Name:</strong> ${data.name} ${data.surname}<br>
                                        <strong>Email:</strong> ${data.email}</p>`;

                    if (data.purchases && data.purchases.length > 0) {
                        customerInfo += "<h4>Purchases:</h4><ul>";
                        data.purchases.forEach(purchase => {
                            customerInfo += `<li><strong>Purchase ID:</strong> ${purchase.purchase_id} 
                                             <br><strong>Total Price:</strong> $${purchase.total_price}</li>`;
                        });
                        customerInfo += "</ul>";
                    } else {
                        customerInfo += "<p>No purchases found for this customer.</p>";
                    }

                    resultsDiv.innerHTML = customerInfo;
                }
            })
            .catch(error => {
                console.error("Error searching customer:", error);
                resultsDiv.innerHTML = `<p style="color: red;">Error retrieving customer data.</p>`;
            });
    });

});
