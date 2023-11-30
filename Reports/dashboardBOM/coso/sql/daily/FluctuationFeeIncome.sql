/*Daily - BOM - CoSo*/

/*Fluctuation - Fee Income (Biến động phí giao dịch) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = (
	SELECT [Date] FROM (
		SELECT ROW_NUMBER() OVER (ORDER BY [Date] DESC) [No], [Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
	) [z] WHERE [No] = 180
);


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
	FROM [Date]
	WHERE [Work] = 1
		AND [Date] BETWEEN @Since AND @Date
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
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
	[Index].[Date]
	, ISNULL(SUM([RawResult].[FeeIncome]), 0) [Value]
FROM [Index]
LEFT JOIN [RawResult]
	ON [RawResult].[Date] = [Index].[Date]
	AND [RawResult].[BranchID] = [Index].[BranchID]
GROUP BY [Index].[Date]
ORDER BY [Index].[Date]


END
