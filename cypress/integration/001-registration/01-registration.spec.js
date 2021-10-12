describe('Registration page test', () => {
    it('Should open registration page', () => {
        cy.visit('http://localhost:5000');
    });

    it('Should catch missing field error', () => {
        cy.get('#submit-btn').click();
        cy.get('.missing').should("be.visible");
    });

    it('Should check registration page is loaded', () => {
        cy.url().should('include', 'registration')
    });

    it('Check h1 & title with text Registration', () => {
        cy.get('h1').should('be.visible');
        cy.title().should('include', 'Registration');
    });

    it('Fill Website name field', () => {
        cy.get('#website-name').clear();
        cy.get('#website-name').type('Cypress test');
    });

    it('Fill Website url field', () => {
        cy.get('#website-url').clear();
        cy.get('#website-url').type('http://localhost:8080');
    });

    it('Selects time zone', () => {
        cy.get('#timezone');
    });

    it('Fill Main Language (long) field', () => {
        cy.get('#main-language-long').clear();
        cy.get('#main-language-long').type('English');
    });

    it('Should change timezone', () => {
        cy.get('#timezone').select('Europe/Tallinn');
        cy.get('#timezone').should('have.value', 'Europe/Tallinn');
        cy.get('#timezone').should('not.have.value', 'UTC');
    })

    it('Fill Main Language (short) field', () => {
        cy.get('#main-language-short').clear();
        cy.get('#main-language-short').type('en');
    });

    it('Fill username', () => {
        cy.get('#admin-name').clear();
        cy.get('#admin-name').type('admin');
    })

    it('Should catch weak password field error', () => {
        cy.get('#admin-password').clear();
        cy.get('#admin-password').type('admin');
        cy.get('#submit-btn').click();
        cy.get('.password').should("be.visible");
    });

    it('Should register properly', () => {
        cy.fixture('user').then(user => {
            const username = user.username;
            const password = user.password;

            cy.get('#admin-name').clear();
            cy.get('#admin-name').type(username);

            cy.get('#admin-password').clear();
            cy.get('#admin-password').type(password);

            cy.get('#submit-btn').click();
            cy.url().should('include', 'login');
        });
    });

    it('Should redirect to login in second registration', () => {
        cy.visit('http://localhost:5000/registration');
        cy.url().should('include', 'login');
    });
});