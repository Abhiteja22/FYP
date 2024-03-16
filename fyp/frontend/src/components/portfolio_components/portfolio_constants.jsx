export const marks = [
    {
      value: 0,
      label: 'Most Risk',
    },
    {
      value: 4,
      label: 'Least Risk',
    },
  ];
export const options = [
    { value: '^GSPC', label: 'General' },
    { value: '^DJUSFN', label: 'Finance' },
    { value: '^NBI', label: 'Healthcare' },
    { value: '^NDXT', label: 'Technology' },
    { value: '^SPSITE', label: 'Telecommunications' },
    { value: '^DJUSBM', label: 'Basic Materials' },
    { value: '^DJUSIN', label: 'Industrials' },
    { value: 'XLP', label: 'Consumer Staples' },
    { value: '^DJUSUT', label: 'Utilities' },
    { value: '^DJUSRE', label: 'Real Estate' },
    { value: '^GSPE', label: 'Energy' },
    { value: '^SP500-25', label: 'Consumer Discretionary' },
];
export const timeOptions = [
    { value: '1month', label: 'Very Short (1 Month)' },
    { value: '3month', label: 'Short (3 Months)' },
    { value: '6month', label: 'Short (6 Months)' },
    { value: '1year', label: 'Normal (1 Year)' },
    { value: '3year', label: 'Short-Mid (3 Years)' },
    { value: '5year', label: 'Mid (5 Years)' },
    { value: '10year', label: 'Long (10 Year)' },
    { value: '30year', label: 'Retirement (30 Years)' },
];
export const defaultValues = {
  name: 'untitled',
  risk_aversion: 1.00,
  market_index: '^GSPC',
  sector: 'General',
  investment_time_period: '1year',
}