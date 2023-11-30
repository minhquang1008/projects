/*MTD - BOM - CoSo*/

/*Fluctuation - Fee Income (Biến động phí giao dịch)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [WorkDays] AS (
	SELECT
		[Date]
		, CASE 
			WHEN ISDATE(CONCAT(YEAR([Date]),'-',MONTH([Date]),'-',DAY(@Date))) = 1 
				THEN DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),DAY(@Date),0,0,0,0)
			ELSE EOMONTH(DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),1,0,0,0,0)) 
		END [EndOfPeriod]
	FROM [Date]
	WHERE [Work] = 1
		AND [Date] BETWEEN @Since AND @Date
		AND DAY([Date]) <= DAY(@Date)
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
		, [WorkDays].[EndOfPeriod]
		, [TargetByBranch].[BranchID]
	FROM [TargetByBranch] CROSS JOIN [WorkDays]
)

, [RawResult] AS (
	SELECT
		[trading_record].[date] [Date]
		, [relationship].[branch_id] [BranchID]
		, ISNULL(SUM([trading_record].[fee]), 0) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [trading_record].[Date]
		AND [trading_record].[sub_account] = [relationship].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY [trading_record].[date], [relationship].[branch_id]
)

SELECT
	[Index].[EndOfPeriod] [Date]
	, ISNULL(SUM([RawResult].[FeeIncome]), 0) [Value]
FROM [Index]
LEFT JOIN [RawResult]
	ON [RawResult].[Date] = [Index].[Date]
	AND [RawResult].[BranchID] = [Index].[BranchID]
GROUP BY [Index].[EndOfPeriod]
ORDER BY [Index].[EndOfPeriod]


END
