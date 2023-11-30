/*Daily - BOM - PhaiSinh*/

/*Fluctuation - Fee Income (Biến động phí giao dịch)*/

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
	SELECT [BranchID]
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

, [Rel] AS (
    SELECT DISTINCT
        [date] [Date]
        , [account_code] [AccountCode]
        , [branch_id] [BranchID]
        , [broker_id] [BrokerID]
    FROM [relationship]
    WHERE [date] BETWEEN @Since AND @Date
)

, [RawResult] AS (
	SELECT
		[RRE0018].[Ngay] [Date]
		, [Rel].[BranchID]
		, ISNULL(SUM([RRE0018].[PhiGiaoDichPHSThu]), 0) [FeeIncome]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [RRE0018].[Ngay] = [Rel].[Date]
		AND [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
	GROUP BY [RRE0018].[Ngay], [Rel].[BranchID]
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
