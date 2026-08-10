import XCTest

final class LoginUITests: XCTestCase {
    func testValidLoginShowsDashboard() {
        let app = XCUIApplication()
        app.launchArguments += ["-ui-testing", "-stub-network"]
        app.launch()
        let email = app.textFields["email"]
        XCTAssertTrue(email.waitForExistence(timeout: 5))
        email.tap(); email.typeText("qa@example.test")
        let password = app.secureTextFields["password"]
        password.tap(); password.typeText("test-password")
        app.buttons["Sign in"].tap()
        XCTAssertTrue(app.staticTexts["Dashboard"].waitForExistence(timeout: 5))
    }
}
