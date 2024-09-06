// This is the Geb configuration file.
// See: http://www.gebish.org/manual/current/#configuration


import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.firefox.FirefoxOptions
import org.openqa.selenium.remote.DesiredCapabilities
import org.openqa.selenium.remote.CapabilityType


import io.github.bonigarcia.wdm.WebDriverManager
import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.firefox.FirefoxDriver

waiting {
  timeout = 20
}

environments {
  // run via “./gradlew chromeTest”
  // See: http://code.google.com/p/selenium/wiki/ChromeDriver
  chrome {
    driver = {
      // Use WebDriverManager to manage ChromeDriver
      WebDriverManager.chromedriver().setup()

      ChromeOptions o = new ChromeOptions()
      o.addArguments('--no-sandbox');
      o.addArguments('--disable-dev-shm-usage');
      o.addArguments("--ignore-certificate-errors");
      DesiredCapabilities cap=DesiredCapabilities.chrome();
      cap.setCapability(ChromeOptions.CAPABILITY, o);
      cap.setCapability(CapabilityType.ACCEPT_SSL_CERTS, true);
      cap.setCapability(CapabilityType.ACCEPT_INSECURE_CERTS, true);
      new ChromeDriver(cap);
    }
    
  }

  firefox {
        atCheckWaiting = 1
        driver = {
            // Use WebDriverManager to manage GeckoDriver
            WebDriverManager.firefoxdriver().setup()

            FirefoxOptions options = new FirefoxOptions()
            options.setCapability("marionette", true)  // Ensure Marionette is enabled
            
            new FirefoxDriver(options)
        }
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
  //firefox {
  //  atCheckWaiting = 1
  //  driver = { new FirefoxDriver() }
  //}
}

// To run the tests with all browsers just run “./gradlew test”
baseUrl = "http://gebish.org"
