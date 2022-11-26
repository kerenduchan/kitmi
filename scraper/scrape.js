import { CompanyTypes, createScraper } from 'israeli-bank-scrapers';

const success = await run();
if(!success) {
    process.exit(1)
}

async function run() {

    const companyIdsMap = new Map();
    companyIdsMap.set('max', CompanyTypes.max);
    companyIdsMap.set('leumi', CompanyTypes.leumi);

    // args validation
    if (process.argv.length != 6 && process.argv.length != 7) {
        console.error("4 or 5 args expected: <company> <start_date> <username> <password> [show]");
        return false;
    }

    // whether or not to show the browser
    let showBrowser = false;
    if (process.argv.length == 7) {
        if(process.argv[6] == "show") {
            showBrowser = true;
        }
        else {
            console.error("optional 5th arg must be 'show'");
            return false;
        }
    }

    // company (max/leumi)
    const companyStr = process.argv[2];
    const companyId = companyIdsMap.get(companyStr);
    if (companyId === undefined) {
        console.error("unrecognized company: '" + companyStr + "'");
        console.error("Should be one of: " + Array.from(companyIdsMap.values()).join(' '));
        return false;
    }

    // start date
    const dateStr = process.argv[3];
    const tmp = Date.parse(dateStr); // '2020-05-01'
    if (isNaN(tmp)) {
        console.error("invalid date '" + dateStr + "'");
        return false;
    }
    const startDate = new Date(tmp);

    // scrape
    return scrape(companyId, startDate, process.argv[4], process.argv[5], showBrowser);
}

async function scrape(companyId, startDate, username, password, showBrowser) {
    try {
        const options = {
            companyId,
            startDate,
            combineInstallments: false,
            showBrowser
        };

        const credentials = {
            username,
            password
        };

        const scraper = createScraper(options);
        const scrapeResult = await scraper.scrape(credentials);

        if (scrapeResult.success) {
            scrapeResult.accounts.forEach((account) => {
                console.log(JSON.stringify(account.txns, null, 2));
            });
        }
        else {
            throw new Error(scrapeResult.errorType);
        }
    } catch (e) {
        console.error(`scraping failed for the following reason: ${e.message}`);
        return false;
    }
    return true;
};