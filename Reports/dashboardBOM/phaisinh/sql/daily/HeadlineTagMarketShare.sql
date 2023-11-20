/*Daily - BOM - PhaiSinh*/

/*Headline Tag - Market Share (Phần trăm hoàn thành chỉ tiêu ngày - Thị phần) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

DECLARE @PrevTotalContracts DECIMAL(30,2);
SET @PrevTotalContracts = (
	SELECT
		SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] = @Prev
);

DECLARE @TodayTotalContracts DECIMAL(30,2);
SET @TodayTotalContracts = (
	SELECT
		SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] = @Date
);

WITH 

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [Rel] AS (
	SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
	WHERE [date] IN (@Prev, @Date)
)

, [PrevMarketShare] AS (
	SELECT
		SUM([RRE0018].[SoLuongHopDong]) / @PrevTotalContracts / 2 [MarketShare]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] = @Prev
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

, [TodayMarketShare] AS (
	SELECT
		SUM([RRE0018].[SoLuongHopDong]) / @TodayTotalContracts / 2 [MarketShare]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] = @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [TargetByBranch])
)

SELECT
	[TodayMarketShare].[MarketShare] [MarketShare]
	, [TodayMarketShare].[MarketShare] - [PrevMarketShare].[MarketShare] [AbsoluteChange]
	, CASE 
		WHEN [PrevMarketShare].[MarketShare] = 0 THEN 0
		ELSE [TodayMarketShare].[MarketShare] / [PrevMarketShare].[MarketShare] - 1
	END [RelativeChange]
FROM [PrevMarketShare]
CROSS JOIN [TodayMarketShare]


END

