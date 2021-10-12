describe('Login page test', () => {
    // unsuccessful login
    it('Blank fields should get error', () => {
        cy.visit('http:127.0.0.1:5000/login');
        cy.get('#name').type("");
        cy.get('#password').type("");
        cy.get('#login-btn').click();
    });

    it('Blank password field should get error', () => {
        cy.visit('http:127.0.0.1:5000/login');
        cy.get('#name').type("admin");
        cy.get('#password').type("");
        cy.get('#login-btn').click();
    });

    it('Non-existing user should get error', () => {
        cy.visit('http:127.0.0.1:5000/login');
        cy.get('#name').type("user");
        cy.get('#password').type("user");
        cy.get('#login-btn').click();
    });
    // successful login
    it('Should log in successfully', () => {
        cy.fixture('user').then(user => {
            cy.get('#name').type(user.username);
            cy.get('#password').type(user.password);
            cy.get('#login-btn').click();
        });
    });
});