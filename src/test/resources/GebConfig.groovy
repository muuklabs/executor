// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration

import java.net.URL;

import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.remote.DesiredCapabilities
import org.openqa.selenium.remote.CapabilityType

//WDM to use on Selenium3
//import io.github.bonigarcia.wdm.WebDriverManager;

waiting {
  timeout = 20
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver

  chrome {
    driver = {
        ChromeOptions options = new ChromeOptions()
        new ChromeDriver(options)
    }
  }

  chromeWDM {
    //Download and configure ChromeDriver using https://github.com/bonigarcia/webdrivermanager
    WebDriverManager.chromedriver().setup()
    WebDriver driver = new ChromeDriver()
  }

  // run via “./gradlew chromeHeadlessTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chromeHeadless {
    driver = {
      ChromeOptions o = new ChromeOptions()
      o.addArguments('headless')
      new ChromeDriver(o)
    }
  }

  // run via “./gradlew firefoxTest”
  // See: http://code.google.com/p/selenium/wiki/FirefoxDriver
  firefox {
    atCheckWaiting = 1
    driver = { new FirefoxDriver() }
  }

}

// To run the tests with all browsers just run “./gradlew test”
baseUrl = "http://gebish.org"
