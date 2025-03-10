document.addEventListener("DOMContentLoaded", function () {
    // Add Product Form
    const addProductForm = document.getElementById("add-product-form");
    const productMessageDiv = document.getElementById("product-message");

    if (addProductForm) {
        addProductForm.addEventListener("submit", async function (event) {
            event.preventDefault(); // Prevent default form submission

            if (!addProductForm.checkValidity()) {
                productMessageDiv.style.display = "block";
                productMessageDiv.innerHTML = `<p style="color: red;">Please fill out all required fields.</p>`;
                return;
            }

            // Get form data
            const formData = new FormData(addProductForm);
            const data = {
                product_name: formData.get("product_name"),
                price: formData.get("price"),
                available_amount: formData.get("available_amount")
            };

            try {
                const response = await fetch("/add-product", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                // Display success or error message
                productMessageDiv.style.display = "block";
                if (response.ok) {
                    productMessageDiv.innerHTML = `<p style="color: green;">${result.message}</p>`;
                    addProductForm.reset(); // Reset form fields
                } else {
                    productMessageDiv.innerHTML = `<p style="color: red;">${result.error}</p>`;
                }
            } catch (error) {
                productMessageDiv.style.display = "block";
                productMessageDiv.innerHTML = `<p style="color: red;">Error submitting form: ${error.message}</p>`;
            }
        });
    }

    // Make Purchase Form
    const makePurchaseForm = document.getElementById("make-purchase-form");
    const purchaseResultsDiv = document.getElementById("purchase-results").querySelector("blockquote");

    if (makePurchaseForm) {
        makePurchaseForm.addEventListener("submit", async function (event) {
            event.preventDefault(); // Prevent default form submission

            // Collect form data
            const formData = new FormData(makePurchaseForm);
            const customerEmail = formData.get("customer_email");
            const productName = formData.get("product_name"); // Fixed typo from "product_namr"
            const amountToPurchase = formData.get("amount_to_purchase");

            // Validate inputs
            if (!customerEmail || !productName || !amountToPurchase) {
                purchaseResultsDiv.innerHTML = "<p style='color: red;'>All fields are required!</p>";
                return;
            }

            // Send data via fetch API
            try {
                const response = await fetch("/make-purchase", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        customer_email: customerEmail,
                        product_name: productName,
                        amount_to_purchase: amountToPurchase
                    })
                });

                const data = await response.json();

                // Display result
                if (response.ok) {
                    purchaseResultsDiv.innerHTML = `<p style='color: green;'>${data.message}</p>`;
                    makePurchaseForm.reset(); // Reset form fields
                } else {
                    purchaseResultsDiv.innerHTML = `<p style='color: red;'>Error: ${data.error}</p>`;
                }
            } catch (error) {
                purchaseResultsDiv.innerHTML = `<p style='color: red;'>Failed to process purchase.</p>`;
                console.error("Error:", error);
            }
        });
    }
});
