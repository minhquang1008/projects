/*MTD - BOM - CoSo*/

/*Trailing - Fee Income*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH 

[BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [MonthlyTarget] AS (
    SELECT 
		[Year]
        , CAST(SUM(CAST([Target] AS FLOAT)) / 12 AS DECIMAL(30,8)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
		AND [Measure] = 'Fee Income'
	GROUP BY [Year]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		EOMONTH([trading_record].[date]) [Date]
		, ISNULL(SUM([trading_record].[fee]), 0) [Actual]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [trading_record].[date]
		AND [relationship].[sub_account] = [trading_record].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchList])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY EOMONTH([trading_record].[date])
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Actual]
	, [MonthlyTarget].[Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
ORDER BY 1


END