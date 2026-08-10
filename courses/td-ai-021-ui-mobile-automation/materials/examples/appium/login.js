const { remote } = require('webdriverio');

async function main() {
  const driver = await remote({ hostname: '127.0.0.1', port: 4723, path: '/',
    capabilities: { platformName: 'Android', 'appium:automationName': 'UiAutomator2',
      'appium:appPackage': 'com.example.app', 'appium:appActivity': '.MainActivity' } });
  try {
    await (await driver.$('id=com.example.app:id/email')).setValue('qa@example.test');
    await (await driver.$('id=com.example.app:id/password')).setValue('test-password');
    await (await driver.$('~Sign in')).click();
    await (await driver.$('~Dashboard')).waitForDisplayed({ timeout: 10000 });
  } finally { await driver.deleteSession(); }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
