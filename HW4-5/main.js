require("../opendsu-sdk/psknode/bundles/openDSU");

const readline = require("readline");
const openDSU = require("opendsu");
const resolver = openDSU.loadApi("resolver");
const keyssispace = openDSU.loadApi("keyssi");

async function authenticateUser(username) {
    const templateSSI = keyssispace.createTemplateSeedSSI("default");

    // Create or load user-specific DSU
    return new Promise((resolve, reject) => {
        resolver.loadDSU(username, (err, dsu) => {
            if (err) {
                resolver.createDSU(templateSSI, (err, newDSU) => {
                    if (err) {
                        reject(err);
                    } else {
                        newDSU.writeFile("/username", username, (err) => {
                            if (err) {
                                reject(err);
                            } else {
                                resolve(newDSU);
                            }
                        });
                    }
                });
            } else {
                resolve(dsu);
            }
        });
    });
}

function addItem(dsu, name, description, price, link) {
    const item = {
        name,
        description,
        price,
        link,
        purchased: false
    };

    dsu.readFile("/wishlist", (err, data) => {
        let wishlist = [];

        if (!err && data) {
            wishlist = JSON.parse(data.toString());
        }

        wishlist.push(item);

        dsu.writeFile("/wishlist", JSON.stringify(wishlist), (err) => {
            if (err) {
                console.error("Error writing item to wishlist:", err);
            } else {
                console.log("Item added successfully!");
            }
        });
    });
}

function viewItems(dsu) {
    dsu.readFile("/wishlist", (err, data) => {
        if (err) {
            console.error("Error reading wishlist:", err);
        } else {
            const wishlist = JSON.parse(data.toString());
            wishlist.forEach((item, index) => {
                console.log(`Item ${index + 1}: ${item.name} - ${item.description} - $${item.price} - ${item.link} - ${item.purchased ? "Purchased" : "Not purchased"}`);
            });
        }
    });
}

function markItem(dsu, itemIndex) {
    dsu.readFile("/wishlist", (err, data) => {
        if (err) {
            console.error("Error reading wishlist:", err);
        } else {
            const wishlist = JSON.parse(data.toString());

            if (itemIndex >= 0 && itemIndex < wishlist.length) {
                wishlist[itemIndex].purchased = true;

                dsu.writeFile("/wishlist", JSON.stringify(wishlist), (err) => {
                    if (err) {
                        console.error("Error updating item status:", err);
                    } else {
                        console.log("Item marked as purchased!");
                    }
                });
            } else {
                console.log("Invalid item index. Please try again.");
            }
        }
    });
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function main() {
    rl.question("Enter your username: ", async (username) => {
        const dsu = await authenticateUser(username);
        handleCommands(dsu);
    });
}

function handleCommands(dsu) {
    rl.question("Enter command (add/view/mark/exit): ", (command) => {
        switch (command) {
            case "add":
                rl.question("Enter item name: ", (name) => {
                    rl.question("Enter item description: ", (description) => {
                        rl.question("Enter item price: ", (price) =>
                            rl.question("Enter item link: ", (link) => {
                                addItem(dsu, name, description, price, link);
                                handleCommands(dsu);
                            }));
                    });
                });
                break;
            case "view":
                viewItems(dsu);
                handleCommands(dsu);
                break;
            case "mark":
                rl.question("Enter the item index to mark as purchased: ", (itemIndex) => {
                    markItem(dsu, parseInt(itemIndex) - 1);
                    handleCommands(dsu);
                });
                break;
            case "exit":
                console.log("Exiting the Wishlist App. Goodbye!");
                rl.close();
                break;
            default:
                console.log("Invalid command. Please try again.");
                handleCommands(dsu);
                break;
        }
    });
}

main();
