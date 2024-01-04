(function ($) {
    // Begin jQuery
    $(function () {
        // DOM ready
        // If a link has a dropdown, add sub menu toggle.
        $("nav ul li a:not(:only-child)").click(function (e) {
            $(this).siblings(".nav-dropdown").toggle();
            // Close one dropdown when selecting another
            $(".nav-dropdown").not($(this).siblings()).hide();
            e.stopPropagation();
        });
        // Clicking away from dropdown will remove the dropdown class
        $("html").click(function () {
            $(".nav-dropdown").hide();
        });
        // Toggle open and close nav styles on click
        $("#nav-toggle").click(function () {
            $("nav ul").slideToggle();
        });
        // Hamburger to X toggle
        $("#nav-toggle").on("click", function () {
            this.classList.toggle("active");
        });
    }); // end DOM ready
})(jQuery); // end jQuery


$(document).ready(function () {
    var carrito = []; // Lista para almacenar productos en el carrito

    function actualizarListaCarrito() {
        var listaCarrito = $("#lista-carrito");
        listaCarrito.empty(); // Limpiar la lista antes de actualizarla

        // Agregar productos al carrito en la lista
        carrito.forEach(function (producto) {
            var listItem = $("<li></li>");
            listItem.text(producto.nombre + ": $" + producto.precio);

            var botonEliminar = $("<button class='eliminar-item'>Eliminar</button>");
            botonEliminar.data("id", producto.id);

            listItem.append(botonEliminar);
            listaCarrito.append(listItem);
        });
    }

    $(".add-to-cart-btn").on("click", function (e) {
        e.preventDefault();
        var id = $(this).data("id");
        var nombre = $(this).data("nombre");
        var precio = $(this).data("precio");

        // Agregar el producto al carrito
        carrito.push({ id: id, nombre: nombre, precio: precio });

        // Mostrar el carrito actualizado en la consola
        console.log(carrito);

        // Actualizar dinámicamente la lista de productos en el carrito
        actualizarListaCarrito();

        // Mostrar mensaje al usuario (puedes personalizar esto)
        alert("Producto agregado al carrito");
    });

    // Manejar eventos de los botones "Eliminar" utilizando delegación de eventos
    $("#lista-carrito").on("click", ".eliminar-item", function () {
        var idProducto = $(this).data("id");
        eliminarProductoDelCarrito(idProducto);
    });

    // Función para mostrar/ocultar el carrito
    $("#mostrar-carrito").on("click", function () {
        // Actualizar dinámicamente la lista de productos en el carrito al mostrarlo
        actualizarListaCarrito();

        // Mostrar u ocultar el contenedor del carrito
        $("#carrito-container").toggle();
    });

    // Función para cerrar el carrito
    $("#cerrar-carrito").on("click", function () {
        $("#carrito-container").hide();
    });

    // Función para eliminar un producto del carrito
    function eliminarProductoDelCarrito(idProducto) {
        // Implementa aquí la lógica para eliminar el producto del carrito
        // Puede ser mediante AJAX, actualización del estado en el cliente, etc.
        console.log('Eliminar producto con ID:', idProducto);

        // Actualizar la lista después de eliminar un producto
        carrito = carrito.filter(function (producto) {
            return producto.id !== idProducto;
        });

        // Actualizar la vista del carrito
        actualizarListaCarrito();
    }
});
