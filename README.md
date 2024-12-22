# **Makeup Product Web Scraper**

## **Overview**
This repository contains a collection of web scraping scripts built using **Puppeteer**, with **AWS Lambda** for managing a pool of IP addresses and a **Docker rotating proxy** for rotating proxies during scraping. The scripts collect data for **concealer**, **bronzer**, and **foundation/setting powder** from the following e-commerce websites:
- **Amazon**
- **Sephora**
- **YesStyle**
- **Shoppers Drug Mart**

Each script generates **.csv** files with detailed product data for each product type and website.

---

## **Features**
- Scrapes the following product attributes:
  - **Name**
  - **Price**
  - **Rating**
  - **Image URL**
  - **Ingredients List**
  - **Matching Shade**
  - **Product Link**
- Generates separate `.csv` files for:
  - **Concealer products**
  - Products from **Sephora**, **YesStyle**, and **Shoppers Drug Mart**
- Uses **AWS Lambda** to manage a pool of IP addresses to enhance anonymity and bypass rate-limiting.
- Implements a **Docker rotating proxy server** to ensure proxies are rotated effectively during scraping.
- Modular and scalable design for future enhancements.

---

## **Installation**

### **Prerequisites**
Ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v16 or later)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- An [AWS Account](https://aws.amazon.com/)
- [AWS CLI](https://aws.amazon.com/cli/) (v2 or later)

### **Clone the Repository**
```bash
git clone https://github.com/yourusername/makeup-web-scraper.git
cd makeup-web-scraper
